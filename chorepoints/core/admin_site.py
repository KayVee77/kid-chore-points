from django.contrib.admin import AdminSite

class LithuanianAdminSite(AdminSite):
    site_title = "Taškų sistema"
    site_header = "Taškų sistema - Tėvų skydelis"
    index_title = "Valdymo skydelis"
    
    # Additional customization
    site_url = "/"  # Link to view site
    enable_nav_sidebar = True

# Create an instance of the custom admin site
admin_site = LithuanianAdminSite(name='admin')
