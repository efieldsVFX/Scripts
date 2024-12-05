import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path
from src.collectors.reddit_collector import RedditCollector
import pandas as pd
from datetime import datetime
import logging

class RedditAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Content Analyzer")
        self.root.geometry("600x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Subreddit input
        ttk.Label(main_frame, text="Subreddit to analyze:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.subreddit_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.subreddit_var, width=40).grid(row=0, column=1, sticky=tk.W)
        
        # Keywords input
        ttk.Label(main_frame, text="Search keywords (comma-separated):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.keywords_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.keywords_var, width=40).grid(row=1, column=1, sticky=tk.W)
        
        # Post limit input
        ttk.Label(main_frame, text="Maximum posts to collect:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.limit_var = tk.StringVar(value="1000")
        ttk.Entry(main_frame, textvariable=self.limit_var, width=10).grid(row=2, column=1, sticky=tk.W)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to analyze...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Analyze button
        ttk.Button(main_frame, text="Start Analysis", command=self.run_analysis).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Results text area
        self.results_text = tk.Text(main_frame, height=10, width=60)
        self.results_text.grid(row=5, column=0, columnspan=2, pady=10)
        
    def run_analysis(self):
        try:
            subreddit = self.subreddit_var.get().strip()
            keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
            limit = int(self.limit_var.get())
            
            if not subreddit and not keywords:
                messagebox.showerror("Error", "Please enter either a subreddit or search keywords")
                return
                
            self.progress_var.set("Initializing Reddit collector...")
            reddit = RedditCollector()
            all_posts = []
            all_comments = []
            
            # Create output directory
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            
            # Collect subreddit posts if specified
            if subreddit:
                self.progress_var.set(f"Collecting posts from r/{subreddit}...")
                subreddit_posts = reddit.collect_subreddit_posts(subreddit, limit=limit)
                if not subreddit_posts.empty:
                    all_posts.append(subreddit_posts)
            
            # Search for keywords
            for term in keywords:
                self.progress_var.set(f"Searching for term: {term}")
                search_posts = reddit.search_reddit_posts(term, limit=limit)
                if not search_posts.empty:
                    all_posts.append(search_posts)
            
            # Save results
            if all_posts:
                combined_posts = pd.concat(all_posts, ignore_index=True).drop_duplicates(subset=['id'])
                combined_posts.to_csv(output_dir / 'reddit_posts.csv', index=False)
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Analysis Complete!\n\n")
                self.results_text.insert(tk.END, f"Total posts collected: {len(combined_posts)}\n")
                self.results_text.insert(tk.END, f"Data saved to: {output_dir.absolute()}\n")
                self.progress_var.set("Analysis complete!")
            else:
                self.progress_var.set("No posts found!")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.progress_var.set("Analysis failed!")

def main():
    root = tk.Tk()
    app = RedditAnalyzerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
