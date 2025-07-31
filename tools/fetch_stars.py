#!/usr/bin/env python3
"""
Fetch all starred repositories from a GitHub user account.
Extracts comprehensive metadata including README content for analysis.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import click
from github import Github, GithubException
from tqdm import tqdm
import pandas as pd
from pathlib import Path
import requests
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def retry_on_exception(max_retries=3, delay=1, backoff=2):
    """Decorator to retry functions on exceptions with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    logger.warning(f"Attempt {retries} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

class GitHubStarsFetcher:
    def __init__(self, token: str, username: str):
        self.github = Github(token)
        self.username = username
        self.user = self.github.get_user(username)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.partial_file = self.data_dir / "starred_repos_partial.json"
        self.checkpoint_interval = 50  # Save every 50 repositories
        
    @retry_on_exception(max_retries=3, delay=1)
    def fetch_readme_content(self, repo) -> Optional[str]:
        """Fetch README content from repository with retry logic."""
        try:
            # Try multiple common README filenames
            readme_names = ['README.md', 'README.MD', 'readme.md', 'README.rst', 'README.txt']
            
            for readme_name in readme_names:
                try:
                    readme = repo.get_contents(readme_name)
                    if readme:
                        content = readme.decoded_content.decode('utf-8')
                        # Limit to first 5000 chars for analysis
                        return content[:5000]
                except:
                    continue
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch README for {repo.full_name}: {str(e)}")
            return None
    
    @retry_on_exception(max_retries=3, delay=1)
    def extract_repo_info(self, repo) -> Dict:
        """Extract comprehensive information from a repository with retry logic."""
        try:
            # Basic info
            info = {
                'name': repo.name,
                'full_name': repo.full_name,
                'owner': repo.owner.login,
                'description': repo.description or '',
                'url': repo.html_url,
                'homepage': repo.homepage,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'language': repo.language,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                'size': repo.size,
                'default_branch': repo.default_branch,
                'open_issues': repo.open_issues_count,
                'is_fork': repo.fork,
                'archived': repo.archived,
                'disabled': repo.disabled,
                'license': repo.license.name if repo.license else None,
            }
            
            # Get topics
            try:
                topics = repo.get_topics()
                info['topics'] = topics
            except:
                info['topics'] = []
            
            # Get README content
            info['readme_preview'] = self.fetch_readme_content(repo)
            info['has_readme'] = info['readme_preview'] is not None
            
            # AI/ML related flags
            ai_keywords = ['machine-learning', 'deep-learning', 'artificial-intelligence', 
                          'neural-network', 'tensorflow', 'pytorch', 'scikit-learn', 
                          'data-science', 'nlp', 'computer-vision', 'ai', 'ml',
                          'prompt-engineering', 'llm', 'gpt', 'transformer']
            
            # Check if AI/ML related
            text_to_check = f"{info['name']} {info['description']} {' '.join(info['topics'])}"
            info['is_ai_ml_related'] = any(keyword in text_to_check.lower() for keyword in ai_keywords)
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting info from {repo.full_name}: {str(e)}")
            return None
    
    def load_partial_progress(self) -> tuple[List[Dict], int, set]:
        """Load previously saved partial progress."""
        if self.partial_file.exists():
            try:
                with open(self.partial_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    repos = data.get('repositories', [])
                    last_index = data.get('last_index', 0)
                    processed_names = set(data.get('processed_names', []))
                    logger.info(f"Resuming from repository #{last_index + 1}. Already processed {len(repos)} repositories.")
                    return repos, last_index, processed_names
            except Exception as e:
                logger.warning(f"Failed to load partial progress: {str(e)}. Starting fresh.")
        
        return [], 0, set()
    
    def save_partial_progress(self, repos: List[Dict], current_index: int, processed_names: set):
        """Save partial progress to allow resuming."""
        try:
            progress_data = {
                'repositories': repos,
                'last_index': current_index,
                'processed_names': list(processed_names),
                'timestamp': datetime.now().isoformat(),
                'total_processed': len(repos)
            }
            
            with open(self.partial_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved partial progress: {len(repos)} repositories processed")
        except Exception as e:
            logger.error(f"Failed to save partial progress: {str(e)}")
    
    def fetch_all_stars(self) -> List[Dict]:
        """Fetch all starred repositories with incremental saving and resume capability."""
        logger.info(f"Fetching starred repositories for user: {self.username}")
        
        # Load any existing partial progress
        starred_repos, start_index, processed_names = self.load_partial_progress()
        
        try:
            # Get starred repositories
            stars = self.user.get_starred()
            total_stars = stars.totalCount
            logger.info(f"Total starred repositories: {total_stars}")
            
            if start_index > 0:
                logger.info(f"Resuming from repository #{start_index + 1}")
            
            # Convert to list to allow indexing (for resume functionality)
            repos_list = list(stars)
            
            # Process repositories starting from where we left off
            with tqdm(total=total_stars, initial=start_index, desc="Fetching repositories") as pbar:
                for i, repo in enumerate(repos_list[start_index:], start=start_index):
                    try:
                        # Skip if already processed (extra safety)
                        if repo.full_name in processed_names:
                            pbar.update(1)
                            continue
                        
                        repo_info = self.extract_repo_info(repo)
                        if repo_info:
                            starred_repos.append(repo_info)
                            processed_names.add(repo.full_name)
                        
                        pbar.update(1)
                        
                        # Save progress every checkpoint_interval repositories
                        if (len(starred_repos)) % self.checkpoint_interval == 0:
                            self.save_partial_progress(starred_repos, i, processed_names)
                        
                        # Rate limiting - GitHub allows 5000 requests/hour with auth
                        # But let's be conservative to avoid hitting limits
                        time.sleep(0.2)  # Slightly more conservative
                        
                    except Exception as e:
                        logger.error(f"Error processing repository at index {i}: {str(e)}")
                        # Continue with next repository instead of failing completely
                        pbar.update(1)
                        continue
                    
        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            # Save progress before re-raising
            if starred_repos:
                self.save_partial_progress(starred_repos, len(starred_repos) - 1, processed_names)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            # Save progress before re-raising
            if starred_repos:
                self.save_partial_progress(starred_repos, len(starred_repos) - 1, processed_names)
            raise
        
        # Clean up partial file on successful completion
        if self.partial_file.exists():
            try:
                self.partial_file.unlink()
                logger.info("Cleaned up partial progress file after successful completion")
            except Exception as e:
                logger.warning(f"Failed to clean up partial file: {str(e)}")
        
        return starred_repos
    
    def save_data(self, repos: List[Dict]):
        """Save fetched data in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.data_dir / f"starred_repos_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(repos, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON data to: {json_file}")
        
        # Save as CSV
        df = pd.DataFrame(repos)
        csv_file = self.data_dir / f"starred_repos_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"Saved CSV data to: {csv_file}")
        
        # Save latest symlink
        latest_json = self.data_dir / "starred_repos_latest.json"
        latest_csv = self.data_dir / "starred_repos_latest.csv"
        
        # Remove old symlinks if they exist
        for f in [latest_json, latest_csv]:
            if f.exists() or f.is_symlink():
                f.unlink()
        
        # Create new symlinks
        latest_json.symlink_to(json_file.name)
        latest_csv.symlink_to(csv_file.name)
        
        # Print summary statistics
        logger.info(f"\nSummary:")
        logger.info(f"Total repositories: {len(repos)}")
        logger.info(f"AI/ML related: {sum(1 for r in repos if r.get('is_ai_ml_related', False))}")
        logger.info(f"Languages: {df['language'].value_counts().head(10).to_dict()}")
        
        return json_file, csv_file


@click.command()
@click.option('--token', envvar='GITHUB_TOKEN', required=True, help='GitHub personal access token')
@click.option('--username', default='W3STY11', help='GitHub username')
@click.option('--output-dir', default='data', help='Output directory for data files')
@click.option('--resume', is_flag=True, help='Resume from partial progress if available')
def main(token: str, username: str, output_dir: str, resume: bool):
    """Fetch all starred repositories from GitHub with incremental saving and resume capability."""
    
    # Create fetcher instance
    fetcher = GitHubStarsFetcher(token, username)
    
    # Check for existing partial progress
    if not resume and fetcher.partial_file.exists():
        logger.warning(f"Partial progress file found at {fetcher.partial_file}")
        logger.warning("Use --resume flag to continue from where you left off, or delete the file to start fresh.")
        if not click.confirm("Do you want to resume from partial progress?"):
            if click.confirm("Delete partial progress and start fresh?"):
                fetcher.partial_file.unlink()
                logger.info("Partial progress file deleted. Starting fresh.")
            else:
                logger.info("Exiting. Use --resume to continue or delete the partial file.")
                return
    
    try:
        # Fetch all starred repositories
        repos = fetcher.fetch_all_stars()
        
        # Save the data
        if repos:
            fetcher.save_data(repos)
            logger.info(f"\nSuccessfully fetched {len(repos)} repositories!")
        else:
            logger.warning("No repositories fetched.")
            
    except KeyboardInterrupt:
        logger.info("\nOperation interrupted by user. Progress has been saved.")
        logger.info(f"Use --resume flag to continue from where you left off.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"Progress has been saved. Use --resume flag to continue.")
        raise


if __name__ == "__main__":
    main()