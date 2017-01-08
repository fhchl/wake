# Wake

Scripts to powers your Mac on and play some music at a specific time.

### Usage

Set the alarm:

	python wake.py

Clear all alarms:

	python turn_it_off.py

List alarms:

	python list_alarms.py

The Mac powers on three minutes before the alarm gets off. At the alarm time the script `al.scpt` is executed. It plays your iTunes playist `WAKEMEUP` with a slowly increasing volume.

Please don't rely on this alarm when you really have to get up. Don't forget to plug in your power connection as otherwise the mac won't wake up. 