#!/bin/sh

. bin/activate

cd examples

export FLASK_APP=auth_basic
#export FLASK_APP=auth_database
#export FLASK_APP=auth_withrole
#export FLASK_APP=email_account
#export FLASK_APP=starter_1

export FLASK_ENV=development

flask run
