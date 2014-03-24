from django.db import connection

class Subdomains:
    def process_request(self, request):
        """Inject subdomain information into request"""
        host = request.get_host()
        parts = host.split('.')
        if len(parts) > 2:
            subdomain = u'.'.join(parts[:-2])
            try:
                from django.conf.settings import MAIN_SUBDOMAIN
                if subdomain in MAIN_SUBDOMAIN:
                    subdomain = None
            except ImportError:
                pass
        else:
            subdomain = None
        request.subdomain = subdomain
        schema = 'account_%s' % subdomain
        cursor = connection.cursor()
        cursor.execute("SET search_path TO %s, public" % schema)
        return None
