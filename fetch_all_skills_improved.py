#!/usr/bin/env python3
"""
Fetch ALL skills from skills.sh API with pagination and progress saving
"""

import requests
import json
import time
import signal
import sys

class SkillsFetcher:
    def __init__(self):
        self.all_skills = []
        self.limit = 100
        self.offset = 0
        self.output_file = 'skills_sh_all.json'

    def save_progress(self):
        """Save current progress to file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_count': len(self.all_skills),
                'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'offset': self.offset,
                'skills': self.all_skills
            }, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Progress saved: {len(self.all_skills)} skills")

    def fetch_all_skills(self, max_iterations=100):
        """Fetch all skills using the API with pagination"""

        print("Fetching skills from skills.sh API...")
        print("=" * 60)

        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print("\n\n⚠️  Interrupted! Saving progress...")
            self.save_progress()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        for iteration in range(max_iterations):
            try:
                # Make API request
                url = f"https://skills.sh/api/skills?limit={self.limit}&offset={self.offset}"
                print(f"[{iteration+1}] Fetching offset={self.offset}...")

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.json()
                skills = data.get('skills', [])

                if not skills:
                    print("\n✅ No more skills found!")
                    break

                self.all_skills.extend(skills)
                total_fetched = len(self.all_skills)

                print(f"     → Got {len(skills)} skills (total: {total_fetched})")

                # Show last skill as sample
                if skills:
                    last_skill = skills[-1]
                    print(f"     → Last: {last_skill.get('name', 'unknown')} ({last_skill.get('installs', 0)} installs)")

                # If we got fewer skills than the limit, we've reached the end
                if len(skills) < self.limit:
                    print("\n✅ Reached the end of skills list!")
                    break

                # Move to next page
                self.offset += self.limit

                # Save progress every 500 skills
                if total_fetched % 500 == 0:
                    self.save_progress()

                # Small delay to be respectful to the API
                time.sleep(0.1)

            except requests.exceptions.Timeout:
                print(f"⚠️  Timeout at offset {self.offset}, retrying...")
                time.sleep(2)
                continue
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                break

        # Final save
        self.save_progress()

        # Print statistics
        self.print_stats()

        return self.all_skills

    def print_stats(self):
        """Print final statistics"""
        print(f"\n{'=' * 60}")
        print(f"📊 Final Statistics:")
        print(f"  Total skills fetched: {len(self.all_skills)}")
        print(f"  Unique names: {len(set(s.get('name', '') for s in self.all_skills))}")

        # Group by installs
        install_ranges = {
            '10000+': 0,
            '1000-9999': 0,
            '100-999': 0,
            '10-99': 0,
            '1-9': 0
        }

        for skill in self.all_skills:
            installs = skill.get('installs', 0)
            if installs >= 10000:
                install_ranges['10000+'] += 1
            elif installs >= 1000:
                install_ranges['1000-9999'] += 1
            elif installs >= 100:
                install_ranges['100-999'] += 1
            elif installs >= 10:
                install_ranges['10-99'] += 1
            else:
                install_ranges['1-9'] += 1

        print(f"\n  Distribution by installs:")
        for range_name, count in install_ranges.items():
            if count > 0:
                print(f"    {range_name}: {count}")

        # Print top 20
        print(f"\n🏆 Top 20 Skills:")
        print("-" * 60)
        sorted_skills = sorted(self.all_skills, key=lambda x: x.get('installs', 0), reverse=True)
        for i, skill in enumerate(sorted_skills[:20], 1):
            name = skill.get('name', 'unknown')
            installs = skill.get('installs', 0)
            print(f"{i:2d}. {name:<45} ({installs:>7,} installs)")

if __name__ == '__main__':
    fetcher = SkillsFetcher()
    fetcher.fetch_all_skills(max_iterations=200)
