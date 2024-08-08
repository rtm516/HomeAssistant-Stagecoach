# HomeAssistant-Stagecoach
Custom component built to bring you bus times for Stagecoach Buses. This was built because buses in my area dont have live times available in [UK Transport integration](https://www.home-assistant.io/integrations/uk_transport/), and time tabled based times were only available using the more expensive `nextbuses` call.

The API usage was reverse engineered from the [Stagecoach Bus App](https://play.google.com/store/apps/details?id=com.stagecoach.stagecoachbus).

## How to install
### Manual
You should take the latest download of the repo.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

## Docs

To get full use of the integration, please visit the [docs](https://bottlecapdave.github.io/HomeAssistant-FirstBus/) and use the entity name `sensor.stagecoach_<<NAME_OF_SENSOR>>_next_bus`.
