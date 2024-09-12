""" 
Module for filtering irrelevant links
"""

filter_dict = {
    "diff_domain_filter": True,
    "img_exts": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
    "lang_indicators": ['lang=', '/fr', '/pt', '/es', '/de', '/jp', '/it'],
    "irrelevant_keywords": [
            '/login', '/signup', '/register', '/contact', 'facebook.com', 'twitter.com', 
            'linkedin.com', 'instagram.com', '.js', '.css',
        ]
}
