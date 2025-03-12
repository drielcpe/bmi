#!/usr/bin/env python3

import statistics as stat
import time
import RPi.GPIO as GPIO

class HX711:
    """
    HX711 represents chip for reading load cells.
    """

    def __init__(self, dout_pin, pd_sck_pin, gain_channel_A=128, select_channel='A'):
        """
        Init a new instance of HX711.

        Args:
            dout_pin (int): Raspberry Pi pin number where the Data pin of HX711 is connected.
            pd_sck_pin (int): Raspberry Pi pin number where the Clock pin of HX711 is connected.
            gain_channel_A (int): Optional, by default value 128. Options (128 || 64).
            select_channel (str): Optional, by default 'A'. Options ('A' || 'B').

        Raises:
            TypeError: If pd_sck_pin or dout_pin are not int type.
        """
        if not isinstance(dout_pin, int):
            raise TypeError('dout_pin must be type int. Received: {}'.format(dout_pin))
        if not isinstance(pd_sck_pin, int):
            raise TypeError('pd_sck_pin must be type int. Received: {}'.format(pd_sck_pin))

        self._pd_sck = pd_sck_pin
        self._dout = dout_pin
        self._gain_channel_A = 0
        self._offset_A_128 = 0  # offset for channel A and gain 128
        self._offset_A_64 = 0  # offset for channel A and gain 64
        self._offset_B = 0  # offset for channel B
        self._last_raw_data_A_128 = 0
        self._last_raw_data_A_64 = 0
        self._last_raw_data_B = 0
        self._wanted_channel = ''
        self._current_channel = ''
        self._scale_ratio_A_128 = 1  # scale ratio for channel A and gain 128
        self._scale_ratio_A_64 = 1  # scale ratio for channel A and gain 64
        self._scale_ratio_B = 1  # scale ratio for channel B
        self._debug_mode = False
        self._data_filter = self.outliers_filter  # default filter

        GPIO.setup(self._pd_sck, GPIO.OUT)  # pin _pd_sck is output only
        GPIO.setup(self._dout, GPIO.IN)  # pin _dout is input only
        self.select_channel(select_channel)
        self.set_gain_A(gain_channel_A)

    def select_channel(self, channel):
        """
        Select the desired channel.

        Args:
            channel (str): The channel to select. Options ('A' || 'B').

        Raises:
            ValueError: If channel is not 'A' or 'B'.
        """
        channel = channel.capitalize()
        if channel not in ['A', 'B']:
            raise ValueError('Parameter "channel" has to be "A" or "B". Received: {}'.format(channel))
        self._wanted_channel = channel
        self._read()
        time.sleep(0.5)

    def set_gain_A(self, gain):
        """
        Set gain for channel A.

        Args:
            gain (int): Gain for channel A (128 || 64).

        Raises:
            ValueError: If gain is different than 128 or 64.
        """
        if gain not in [128, 64]:
            raise ValueError('gain has to be 128 or 64. Received: {}'.format(gain))
        self._gain_channel_A = gain
        self._read()
        time.sleep(0.5)

    def zero(self, readings=30):
        """
        Set the current data as an offset for the channel (tare).

        Args:
            readings (int): Number of readings for mean. Allowed values 1..99.

        Raises:
            ValueError: If readings are not in range 1..99.

        Returns: True if error occurred.
        """
        if not (0 < readings < 100):
            raise ValueError('Parameter "readings" can be in range 1 up to 99. Received: {}'.format(readings))

        result = self.get_raw_data_mean(readings)
        if result is False:
            return True

        if self._current_channel == 'A' and self._gain_channel_A == 128:
            self._offset_A_128 = result
        elif self._current_channel == 'A' and self._gain_channel_A == 64:
            self._offset_A_64 = result
        elif self._current_channel == 'B':
            self._offset_B = result
        else:
            return True
        return False

    def set_offset(self, offset, channel='', gain_A=0):
        """
        Set desired offset for a specific channel and gain.

        Args:
            offset (int): Specific offset for channel.
            channel (str): Optional, by default it is the current channel. Options ('A' || 'B').
            gain_A (int): Optional, by default it is the current gain. Options (128 || 64).

        Raises:
            ValueError: If channel is not ('A' || 'B' || '').
            TypeError: If offset is not int type.
        """
        if not isinstance(offset, int):
            raise TypeError('Parameter "offset" has to be integer. Received: {}'.format(offset))

        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            self._offset_A_128 = offset
        elif channel == 'A' and gain_A == 64:
            self._offset_A_64 = offset
        elif channel == 'B':
            self._offset_B = offset
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                self._offset_A_128 = offset
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                self._offset_A_64 = offset
            else:
                self._offset_B = offset
        else:
            raise ValueError('Parameter "channel" has to be "A" or "B". Received: {}'.format(channel))

    def set_scale_ratio(self, scale_ratio, channel='', gain_A=0):
        """
        Set the ratio for calculating weight in desired units.

        Args:
            scale_ratio (float): Number > 0.0 that is used for conversion to weight units.
            channel (str): Optional, by default it is the current channel. Options ('A' || 'B').
            gain_A (int): Optional, by default it is the current gain. Options (128 || 64).

        Raises:
            ValueError: If channel is not ('A' || 'B' || '').
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            self._scale_ratio_A_128 = scale_ratio
        elif channel == 'A' and gain_A == 64:
            self._scale_ratio_A_64 = scale_ratio
        elif channel == 'B':
            self._scale_ratio_B = scale_ratio
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                self._scale_ratio_A_128 = scale_ratio
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                self._scale_ratio_A_64 = scale_ratio
            else:
                self._scale_ratio_B = scale_ratio
        else:
            raise ValueError('Parameter "channel" has to be "A" or "B". Received: {}'.format(channel))

    def set_data_filter(self, data_filter):
        """
        Set data filter.

        Args:
            data_filter (function): Data filter that takes a list of int numbers and returns a list of filtered int numbers.

        Raises:
            TypeError: If filter is not a function.
        """
        if not callable(data_filter):
            raise TypeError('Parameter "data_filter" must be a function. Received: {}'.format(data_filter))
        self._data_filter = data_filter

    def set_debug_mode(self, flag=False):
        """
        Turn on or off debug mode.

        Args:
            flag (bool): True turns on the debug mode. False turns it off.

        Raises:
            ValueError: If flag is not bool type.
        """
        if not isinstance(flag, bool):
            raise ValueError('Parameter "flag" can be only BOOL value. Received: {}'.format(flag))
        self._debug_mode = flag
        print('Debug mode {}'.format('ENABLED' if flag else 'DISABLED'))

    def _save_last_raw_data(self, channel, gain_A, data):
        """
        Save the last raw data for a specific channel and gain.

        Args:
            channel (str): Channel ('A' || 'B').
            gain_A (int): Gain (128 || 64).
            data (int): Data to save.

        Returns: False if error occurred.
        """
        if channel == 'A' and gain_A == 128:
            self._last_raw_data_A_128 = data
        elif channel == 'A' and gain_A == 64:
            self._last_raw_data_A_64 = data
        elif channel == 'B':
            self._last_raw_data_B = data
        else:
            return False

    def _ready(self):
        """
        Check if data is ready for reading.

        Returns: bool True if ready, else False.
        """
        return GPIO.input(self._dout) == 0

    def _set_channel_gain(self, num):
        """
        Set channel and gain.

        Args:
            num (int): Number of clock pulses to send.

        Returns: bool True if successful, else False.
        """
        for _ in range(num):
            start_counter = time.perf_counter()
            GPIO.output(self._pd_sck, True)
            GPIO.output(self._pd_sck, False)
            end_counter = time.perf_counter()
            if end_counter - start_counter >= 0.00006:
                if self._debug_mode:
                    print('Not enough fast while setting gain and channel')
                    print('Time elapsed: {}'.format(end_counter - start_counter))
                return False
        return True

    def _read(self):
        """
        Read data from HX711.

        Returns: (bool || int) False if error occurred, else the read data.
        """
        GPIO.output(self._pd_sck, False)
        ready_counter = 0
        while not self._ready() and ready_counter <= 40:
            time.sleep(0.01)
            ready_counter += 1
            if ready_counter == 50:
                if self._debug_mode:
                    print('self._read() not ready after 40 trials')
                return False

        data_in = 0
        for _ in range(24):
            start_counter = time.perf_counter()
            GPIO.output(self._pd_sck, True)
            GPIO.output(self._pd_sck, False)
            end_counter = time.perf_counter()
            if end_counter - start_counter >= 0.00006:
                if self._debug_mode:
                    print('Not enough fast while reading data')
                    print('Time elapsed: {}'.format(end_counter - start_counter))
                return False
            data_in = (data_in << 1) | GPIO.input(self._dout)

        if self._wanted_channel == 'A' and self._gain_channel_A == 128:
            if not self._set_channel_gain(1):
                return False
            self._current_channel = 'A'
            self._gain_channel_A = 128
        elif self._wanted_channel == 'A' and self._gain_channel_A == 64:
            if not self._set_channel_gain(3):
                return False
            self._current_channel = 'A'
            self._gain_channel_A = 64
        else:
            if not self._set_channel_gain(2):
                return False
            self._current_channel = 'B'

        if self._debug_mode:
            print('Binary value as received: {}'.format(bin(data_in)))

        if data_in == 0x7fffff or data_in == 0x800000:
            if self._debug_mode:
                print('Invalid data detected: {}'.format(data_in))
            return False

        signed_data = -(data_in ^ 0xffffff) + 1 if data_in & 0x800000 else data_in

        if self._debug_mode:
            print('Converted 2\'s complement value: {}'.format(signed_data))

        return signed_data

    def get_raw_data_mean(self, readings=30):
        """
        Get mean value of readings.

        Args:
            readings (int): Number of readings for mean.

        Returns: (bool || int) False if error occurred, else the mean value.
        """
        backup_channel = self._current_channel
        backup_gain = self._gain_channel_A
        data_list = []
        for _ in range(readings):
            data_list.append(self._read())
        data_mean = False
        if readings > 2 and self._data_filter:
            filtered_data = self._data_filter(data_list)
            if not filtered_data:
                return False
            if self._debug_mode:
                print('data_list: {}'.format(data_list))
                print('filtered_data list: {}'.format(filtered_data))
                print('data_mean:', stat.mean(filtered_data))
            data_mean = stat.mean(filtered_data)
        else:
            data_mean = stat.mean(data_list)
        self._save_last_raw_data(backup_channel, backup_gain, data_mean)
        return int(data_mean)

    def get_data_mean(self, readings=30):
        """
        Get mean value of readings minus offset.

        Args:
            readings (int): Number of readings for mean.

        Returns: (bool || int) False if error occurred, else the mean value.
        """
        result = self.get_raw_data_mean(readings)
        if result is False:
            return False
        if self._current_channel == 'A' and self._gain_channel_A == 128:
            return result - self._offset_A_128
        elif self._current_channel == 'A' and self._gain_channel_A == 64:
            return result - self._offset_A_64
        else:
            return result - self._offset_B

    def get_weight_mean(self, readings=30):
        """
        Get mean value of readings minus offset divided by scale ratio.

        Args:
            readings (int): Number of readings for mean.

        Returns: (bool || float) False if error occurred, else the weight.
        """
        result = self.get_raw_data_mean(readings)
        if result is False:
            return False
        if self._current_channel == 'A' and self._gain_channel_A == 128:
            return float((result - self._offset_A_128) / self._scale_ratio_A_128)
        elif self._current_channel == 'A' and self._gain_channel_A == 64:
            return float((result - self._offset_A_64) / self._scale_ratio_A_64)
        else:
            return float((result - self._offset_B) / self._scale_ratio_B)

    def get_current_channel(self):
        """
        Get the current channel.

        Returns: ('A' || 'B')
        """
        return self._current_channel

    def get_data_filter(self):
        """
        Get the current data filter.

        Returns: The current data filter function.
        """
        return self._data_filter

    def get_current_gain_A(self):
        """
        Get the current gain for channel A.

        Returns: (128 || 64)
        """
        return self._gain_channel_A

    def get_last_raw_data(self, channel='', gain_A=0):
        """
        Get the last raw data for a specific channel and gain.

        Args:
            channel (str): Channel ('A' || 'B'). If not provided, returns the current one.
            gain_A (int): Gain (128 || 64). If not provided, returns the current one.

        Raises:
            ValueError: If channel is not ('A' || 'B' || '') or gain_A is not (128 || 64 || 0).

        Returns: int The last raw data.
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._last_raw_data_A_128
        elif channel == 'A' and gain_A == 64:
            return self._last_raw_data_A_64
        elif channel == 'B':
            return self._last_raw_data_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._last_raw_data_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._last_raw_data_A_64
            else:
                return self._last_raw_data_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                .format(channel, gain_A))

    def get_current_offset(self, channel='', gain_A=0):
        """
        Get the current offset for a specific channel and gain.

        Args:
            channel (str): Channel ('A' || 'B'). If not provided, returns the current one.
            gain_A (int): Gain (128 || 64). If not provided, returns the current one.

        Raises:
            ValueError: If channel is not ('A' || 'B' || '') or gain_A is not (128 || 64 || 0).

        Returns: int The current offset.
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._offset_A_128
        elif channel == 'A' and gain_A == 64:
            return self._offset_A_64
        elif channel == 'B':
            return self._offset_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._offset_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._offset_A_64
            else:
                return self._offset_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                .format(channel, gain_A))

    def get_current_scale_ratio(self, channel='', gain_A=0):
        """
        Get the current scale ratio for a specific channel and gain.

        Args:
            channel (str): Channel ('A' || 'B'). If not provided, returns the current one.
            gain_A (int): Gain (128 || 64). If not provided, returns the current one.

        Returns: int The current scale ratio.
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._scale_ratio_A_128
        elif channel == 'A' and gain_A == 64:
            return self._scale_ratio_A_64
        elif channel == 'B':
            return self._scale_ratio_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._scale_ratio_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._scale_ratio_A_64
            else:
                return self._scale_ratio_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                .format(channel, gain_A))

    def power_down(self):
        """
        Power down the HX711.
        """
        GPIO.output(self._pd_sck, False)
        GPIO.output(self._pd_sck, True)
        time.sleep(0.01)

    def power_up(self):
        """
        Power up the HX711.
        """
        GPIO.output(self._pd_sck, False)
        time.sleep(0.01)

    def reset(self):
        """
        Reset the HX711.

        Returns: True if error encountered.
        """
        self.power_down()
        self.power_up()
        result = self.get_raw_data_mean(6)
        return result is False

    def outliers_filter(self, data_list, stdev_thresh=1.0):
        """
        Filter out outliers from the provided list of int.

        Args:
            data_list ([int]): List of int. It can contain Bool False that is removed.
            stdev_thresh (float): Threshold for standard deviation.

        Returns: list of filtered data.
        """
        data = [num for num in data_list if (num != -1 and num is not False and num is not True)]
        if not data:
            return []

        median = stat.median(data)
        dists_from_median = [abs(measurement - median) for measurement in data]
        stdev = stat.stdev(dists_from_median)
        if stdev:
            ratios_to_stdev = [dist / stdev for dist in dists_from_median]
        else:
            return [median]
        filtered_data = [data[i] for i in range(len(data)) if ratios_to_stdev[i] < stdev_thresh]
        return filtered_data


# Main execution
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)  # Set GPIO pin mode to BCM numbering
    hx = HX711(dout_pin=21, pd_sck_pin=20)  # Create an object
    print(hx.get_raw_data_mean())  # Get raw data reading from HX711
    GPIO.cleanup()  # Clean up GPIO