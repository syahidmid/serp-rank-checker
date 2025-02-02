import re
import pycountry


def sanitize_domain(domain):
    if not domain:
        return domain 
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.rstrip('/')

    return domain


