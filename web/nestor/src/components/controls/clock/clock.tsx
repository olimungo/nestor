import { ButtonOff, ButtonOn, DeviceSelector } from '@components';
import { IotDevice, IotDeviceById } from '@models';
import { useEffect, useState } from 'react';
import styles from './clock.module.css';

type Props = {
    devices: IotDevice[];
    onCommand?: (name: string, command: string) => void;
};

export function Clock(props: Props) {
    const dummyCallback = () => true;
    const { devices, onCommand = dummyCallback } = props;
    const [devicesById, setDevicesById] = useState<IotDeviceById[]>([]);

    useEffect(() => {
        if (devices) {
            const devicesById = devices
                .map((device) => ({
                    id: device.id,
                    netId: device.netId,
                    selected: true,
                }))
                .sort((a, b) => (a.netId > b.netId ? 1 : -1));

            setDevicesById(devicesById);
        }
    }, [devices]);

    const handleCommand = (command: string) => {
        devicesById.forEach((device) => {
            if (device.selected) {
                onCommand(device.id, command);
            }
        });
    };

    return (
        <div className={`${styles.component}`}>
            <div className="text-3xl mt-6 ml-6">CLOCK</div>

            <div className="flex flex-col items-center w-full">
                <div className="m-5">
                    <ButtonOn onClick={() => handleCommand('up')} />
                </div>
                <div className="m-5">
                    <ButtonOff onClick={() => handleCommand('stop')} />
                </div>

                <DeviceSelector
                    devices={devicesById}
                    onChange={(devices) => setDevicesById(devices)}
                />
            </div>
        </div>
    );
}
