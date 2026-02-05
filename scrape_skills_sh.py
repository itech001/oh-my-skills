#!/usr/bin/env python3
"""
Scroll through skills.sh to fetch all skills using Selenium
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def fetch_all_skills_with_selenium():
    """Fetch all skills from skills.sh by scrolling the page."""

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    # Initialize webdriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Opening skills.sh...")
        driver.get("https://skills.sh")

        # Wait for initial content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        print("Scrolling to load all skills...")

        # Track previously loaded skill count
        previous_height = 0
        skill_cards = []
        same_count_iterations = 0
        max_same_iterations = 5  # Stop if no new skills after 5 iterations

        while same_count_iterations < max_same_iterations:
            # Get current page height
            current_height = driver.execute_script("return document.body.scrollHeight")

            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            time.sleep(2)

            # Check if we've reached the end
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == previous_height:
                same_count_iterations += 1
                print(f"No new content (iteration {same_count_iterations}/{max_same_iterations})")
            else:
                same_count_iterations = 0
                previous_height = new_height
                print(f"Scrolled to height: {new_height}px")

            # Try to find skill cards using multiple selectors
            try:
                # Method 1: Look for elements with data-skill-id attribute
                cards = driver.find_elements(By.CSS_SELECTOR, "[data-skill-id]")
                if cards:
                    print(f"Found {len(cards)} skill cards (data-skill-id)")
                else:
                    # Method 2: Look for anchor tags with href containing "/skills/"
                    cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/skills/']")
                    if cards:
                        print(f"Found {len(cards)} skill links (href)")
                    else:
                        # Method 3: Look for common skill card class names
                        cards = driver.find_elements(By.CSS_SELECTOR, "[class*='skill']")
                        print(f"Found {len(cards)} elements with 'skill' in class")

                if len(cards) != len(skill_cards):
                    print(f"Skill count increased: {len(skill_cards)} -> {len(cards)}")
                    skill_cards = cards

            except Exception as e:
                print(f"Error finding skill cards: {e}")

        print(f"\nTotal skills found: {len(skill_cards)}")

        # Extract skill information
        skills = []
        seen_names = set()

        for i, card in enumerate(skill_cards, 1):
            try:
                # Get the outer HTML for parsing
                outer_html = card.get_attribute('outerHTML')

                # Try to extract skill name
                name = ""
                try:
                    # Method 1: Look for text content
                    name = card.text.strip()
                    # Take only first line or first 100 chars
                    name = name.split('\n')[0][:100]
                except:
                    pass

                if not name or name in seen_names or len(name) < 3:
                    continue

                seen_names.add(name)

                # Try to find link/href
                href = ""
                try:
                    href = card.get_attribute('href')
                except:
                    try:
                        link = card.find_element(By.TAG_NAME, "a")
                        href = link.get_attribute('href')
                    except:
                        pass

                skills.append({
                    'name': name,
                    'href': href,
                    'position': i
                })

                if i % 10 == 0:
                    print(f"Processed {i}/{len(skill_cards)} skills...")

            except Exception as e:
                print(f"Error processing card {i}: {e}")
                continue

        print(f"\nExtracted {len(skills)} unique skills")

        # Save to JSON
        output_file = 'skills_sh_scrolled.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_count': len(skills),
                'scrolled_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'skills': skills
            }, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved to {output_file}")

        # Print summary
        print("\n📊 Skills Summary:")
        for skill in skills[:20]:
            print(f"  - {skill['name']}")
        if len(skills) > 20:
            print(f"  ... and {len(skills) - 20} more")

        return skills

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

    finally:
        driver.quit()

if __name__ == '__main__':
    print("=" * 60)
    print("Skills.sh Scraper with Selenium")
    print("=" * 60)
    fetch_all_skills_with_selenium()
