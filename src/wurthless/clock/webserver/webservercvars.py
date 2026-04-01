from wurthless.clock.cvars.cvars import registerCvar

# If True, shutdown display driver while running server. Default is False.
registerCvar("wurthless.clock.webserver",
             "disable_display_when_serving",
             "Boolean",
             False)

# I/O pin that will be pulled high when server mode is active. Default is -1 (disable).
registerCvar("wurthless.clock.webserver",
             "server_active_pin",
             "Int",
             -1)
