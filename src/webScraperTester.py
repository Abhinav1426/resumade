
import requests
from bs4 import BeautifulSoup
from pprint import pprint


def linkedin_scrape_job_details(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return {"error": str(e)}

    soup = BeautifulSoup(response.text, 'lxml')
    job_data = {
        "title": None,
        "company": None,
        "location": None,
        "description": None,
        "posted_or_reposted": None,
        "people_clicked_apply": None
    }
    # Customize these selectors based on the site you're targeting
    job_data["title"] = soup.find("h1") and soup.find("h1").get_text(strip=True)
    job_data["company"] = soup.find("a", {"class": "topcard__org-name-link"}) or \
                          soup.find("div", class_="company")  # fallback
    if job_data["company"]:
        job_data["company"] = job_data["company"].get_text(strip=True)

    job_data["location"] = soup.find("span", class_="topcard__flavor--bullet") or \
                           soup.find("div", class_="location")
    if job_data["location"]:
        job_data["location"] = job_data["location"].get_text(strip=True)
    desc_section = soup.find("div", {"class": "description__text"}) or \
                   soup.find("div", {"id": "jobDescriptionText"})
    if desc_section:
        job_data["description"] = desc_section.get_text(strip=True)
    reposted_tag = soup.find("span", class_="posted-time-ago__text")
    if reposted_tag:
        job_data["posted_or_reposted"] = reposted_tag.get_text(strip=True)

    applicants_tag = soup.find("span", class_="num-applicants__caption")
    if applicants_tag:
        job_data["people_clicked_apply"] = applicants_tag.get_text(strip=True)

    return job_data


if __name__ == '__main__':
    links=[
           'https://www.linkedin.com/jobs/view/4223614572',
           'https://www.linkedin.com/jobs/view/4217209535']
    for i in links:
        job = linkedin_scrape_job_details   (i)
        pprint(job)