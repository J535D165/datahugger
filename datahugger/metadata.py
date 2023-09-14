import requests


class MetaData:
    """MetaData for a resource"""

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
        """Return metadata in RDF representation"""
        return self._get_doi_metadata("application/rdf+xml").text

    def cls(self):
        """Return metadata in CLS representation"""
        return self._get_doi_metadata("application/vnd.citationstyles.csl+json").json()

    def bibtex(self):
        """Return metadata in BibTex representation"""
        return self._get_doi_metadata("application/x-bibtex").text

    def ris(self):
        """Return metadata in RIS representation"""
        return self._get_doi_metadata("application/x-research-info-systems").text

    def citation(self, style=None, locale=None):
        """Return metadata as formatted citation.

        See https://editor.citationstyles.org/searchByName/ for
        an overview of styles.
        """
        content_type = "text/x-bibliography"

        if style:
            content_type += f"; style={style}"
        if locale:
            content_type += f"; locale={locale}"

        return self._get_doi_metadata(content_type).text
