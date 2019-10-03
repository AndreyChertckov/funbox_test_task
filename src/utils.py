import re


def get_domains(links):
    regular_exp = r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)'

    def search_domain(link):
        return re.search(regular_exp, link).group(1)

    return list(map(search_domain, links))
