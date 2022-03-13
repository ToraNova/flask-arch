#!/bin/sh

. ../bin/activate

export FLASK_APP=starter_1
export FLASK_ENV=development

flask run
