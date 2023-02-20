from recherchePDF import recherchePDF

def listgen(tag):
    pdfs = recherchePDF(tag)
    # generate html array from pdfs
    html = []
    for pdf in pdfs:
        text = "{{url_for('static', filename='pdf/" + pdf[0] + ".pdf')}}"
        # text = "<a href={{ url_for('static', filename='pdf/" + pdf[0] + ".pdf') }} download>" + pdf[0] + "</a><br>" + pdf[1]
        print("\n\n", text, "\n\n")
        html.append(text)
    return html