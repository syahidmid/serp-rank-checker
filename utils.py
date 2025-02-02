import re
import pycountry
import langcodes

def sanitize_domain(domain):
    if not domain:
        return domain 
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.rstrip('/')

    return domain


