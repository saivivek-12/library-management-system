import glob
for f in glob.glob('library/templates/*.html'):
    content = open(f).read()
    content = content.replace("{% static 'css/style.css' %}", "{% static 'css/style.css' %}?v=2")
    content = content.replace("{% static 'js/api.js' %}", "{% static 'js/api.js' %}?v=2")
    content = content.replace("{% static 'js/auth.js' %}", "{% static 'js/auth.js' %}?v=2")
    open(f, 'w').write(content)
