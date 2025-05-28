# utils/robot_check.py
import urllib.robotparser

def is_scraping_allowed(url, user_agent='*'):
    rp = urllib.robotparser.RobotFileParser()
    domain = '/'.join(url.split('/')[:3]) + '/robots.txt'
    rp.set_url(domain)
    rp.read()
    return rp.can_fetch(user_agent, url)
