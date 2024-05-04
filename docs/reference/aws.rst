=================
AWS
=================

EventBridge
~~~~~~~~~~~

Settings

.. literalinclude:: ../../example/settings.py
   :start-after: # Start AWS EventBridge Settings
   :end-before: # End AWS EventBridge Settings

Event
#####

.. autoclass:: drf_events.event_handlers.aws.EventBridgeEvent
   :members:

Handler
#######

.. autoclass:: drf_events.event_handlers.aws.EventBridgeEventHandler
   :members: