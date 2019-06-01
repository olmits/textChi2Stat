import time
from flask import render_template, request, flash
from langdetect import detect, lang_detect_exception

from webapp import app
from webapp.texting import CalculateXi2Strategy, text_to_test


@app.route('/', methods=['POST', 'GET'])
@app.route('/output', methods=['POST', 'GET'])
def text_forms_enable():
    start_time = time.time()
    if request.method == 'POST':
        texts = request.form.to_dict()
        try:
            for k, v in texts.items():
                iso2 = detect(v)
                if not k == iso2:
                    flash('Language mismatch: "{0}" was inserted in "{1}" form'.format(iso2, k))
                    return render_template('stats.html', filled_forms=text_to_test)
                treegrams = CalculateXi2Strategy(v, 3, iso2)
                tree = treegrams.calculate_xi2()
                bigrams = CalculateXi2Strategy(v, 2, iso2)
                bi = bigrams.calculate_xi2()
                texts[k] = (tree, bi)
            res_time = time.time() - start_time
            return render_template('stats.html', result=texts, running_time=("--- %s seconds ---" % res_time))
        except lang_detect_exception.LangDetectException as error:
            flash('{0}: fill all fields'.format(error))
            return render_template('stats.html', filled_forms=text_to_test)
    else:
        return render_template('stats.html', filled_forms=text_to_test)
