#!/usr/bin/env python

import bolero
from bolero.app import app

if __name__ == '__main__':
    bolero.app.setup()
    app.run(debug=True)
