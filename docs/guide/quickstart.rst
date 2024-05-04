#############
Quickstart
#############

Create a python virtual environment.

Using pip

.. code-block:: sh

   mkdir drf_events_tutorial
   cd drf_events_tutorial
   pip3 -m venv .venv
   source .venv/activate
   pip3 install django-rest-framework django drf-events

Using poetry

.. code-block:: sh

   mkdir drf_events_tutorial
   cd drf_events_tutorial
   poetry init
   poetry shell
   poetry add django-rest-framework django drf-events

Start a new django project

.. code-block:: sh

   django-admin startproject drf_events_tutorial .

Start a new django app

.. code-block:: sh

   django-admin startapp example_app

Open up `example_app/models.py` and enter the following code

.. literalinclude:: ../../example_app/models.py


Create a new file in `example_app` called `serializers.py` and enter the following code

.. literalinclude:: ../../example_app/serializers.py

Open up `example_app/views.py` and enter the following code

.. literalinclude:: ../../example_app/views.py

Open up `example/urls.py` and enter the following code

.. literalinclude:: ../../example/urls.py

Open up `example/settings.py` and add `rest_framework` and `example_app` to the list of INSTALLED_APPS

.. literalinclude:: ../../example/settings.py
    :start-after: # Application definition
    :end-before: # End application definition
    :language: python

and modify the logging to look like

.. literalinclude:: ../../example/settings.py
   :start-after: # Logging
   :end-before: # End Logging

Run migrations

.. code-block:: sh

   python manage.py makemigrations
   python manage.py migrate

Run the local dev server

.. code-block:: sh

   python manage.py runserver

Open a new terminal and curl the simple model api to see the event

.. code-block:: sh

   curl -X POST http://localhost:8000/simple-model/ \
     -H 'Content-Type: application/json' \
     -d '{"boolean":true,"char_field":"lorem ipsum"}'

Alternatively, visit the browsable api and use the UI to submit a request

.. code-block:: sh

   http://localhost:8000

The following log lines should show up in the terminal with the server running

.. code-block:: sh

   Constructing event
   Emitting event {'view_class': 'SimpleModelViewSet'}
