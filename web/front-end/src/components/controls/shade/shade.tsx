import styles from './shade.module.css';
import { ButtonBigDown, ButtonBigStop, ButtonBigUp, DeviceSelector } from '@components';
import { IotDevice, IotDeviceById } from '@models';
import { useEffect, useState } from 'react';

type Props = {
    devices: IotDevice[];
    onCommand?: (name: string, command: string) => void;
};

export function Shade(props: Props) {
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

    const handleCommand = (command: string) =>
        devicesById.forEach((device) => {
            if (device.selected) {
                onCommand(device.id, command);
            }
        });

    return (
        <div className={`${styles.component}`}>
            <div className="text-3xl mt-6 ml-6">SHADES</div>

            <div className="flex flex-col items-center w-full">
                <div className="mt-5">
                    <ButtonBigUp onClick={() => handleCommand('up')} />
                </div>

                <div className="mt-5">
                    <ButtonBigStop onClick={() => handleCommand('stop')} />
                </div>

                <div className="mt-5">
                    <ButtonBigDown onClick={() => handleCommand('down')} />
                </div>

                <DeviceSelector
                    devices={devicesById}
                    onChange={(devices) => setDevicesById(devices)}
                />
            </div>
        </div>
    );
}
