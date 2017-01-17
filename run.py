#! virtual/bin/python

from app import app
app.run(debug=True, use_reloader=False, host="0.0.0.0")
#app.run(debug=False, host="0.0.0.0")
#app.run()

