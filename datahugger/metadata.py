import requests


class MetaData:
    def __init__(self, resource):
        self.resource = resource

    def _get_doi_metadata(self, content_type):
        r = requests.get(
            f"https://doi.org/{self.resource}",
            headers={"Accept": content_type},
        )
        r.raise_for_status()

        return r

    def rdf(self):
        return self._get_doi_metadata("application/rdf+xml").text

    def cls(self):
        return self._get_doi_metadata("application/vnd.citationstyles.csl+json").json()

    def bibtex(self):
        return self._get_doi_metadata("application/x-bibtex").text

    def ris(self):
        return self._get_doi_metadata("application/x-research-info-systems").text

    def citation(self, style=None, locale=None):
        content_type = "text/x-bibliography"

        if style:
            content_type += "; style=harvard3"
        if locale:
            content_type += "; locale=fr-FR"

        return self._get_doi_metadata(content_type).text
