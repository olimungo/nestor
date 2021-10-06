import styles from './shade.module.css';
import {
    ButtonBigDown,
    ButtonBigStop,
    ButtonBigUp,
    DeviceById,
    ButtonLabel,
} from '@components';
import { DeviceType } from '@declarations';
import { useEffect, useState } from 'react';

type DeviceByIdType = { name: string; selected: boolean };
type Props = {
    devices: DeviceType[];
    onCommand?: (name: string, command: string) => void;
};

export function Shade(props: Props) {
    const dummyCallback = () => true;
    const { devices, onCommand = dummyCallback } = props;
    const [devicesById, setDevicesById] = useState<DeviceByIdType[]>([]);

    useEffect(() => {
        if (devices) {
            const devicesById = devices
                .map((device) => ({
                    name: device.name,
                    selected: true,
                }))
                .sort((a, b) => (a.name > b.name ? 1 : -1));

            setDevicesById(devicesById);
        }
    }, [devices]);

    const changeSelected = (name: string) => {
        setDevicesById((previousState) =>
            previousState.map((device) => {
                if (device.name === name) {
                    return { name, selected: !device.selected };
                }
                return device;
            })
        );
    };

    const handleAllOrNone = (selected: boolean) => {
        setDevicesById((previousState) =>
            previousState.map((device) => {
                return { name: device.name, selected };
            })
        );
    };

    const handleCommand = (command: string) => {
        devicesById.forEach((device) => {
            if (device.selected) {
                onCommand(device.name, command);
            }
        });
    };

    return (
        <div className={`${styles.component}`}>
            <div>SHADES</div>

            <div className="flex flex-col items-center w-full">
                <div className="m-8">
                    <ButtonBigUp onClick={() => handleCommand('up')} />
                </div>
                <div className="m-8">
                    <ButtonBigStop onClick={() => handleCommand('stop')} />
                </div>
                <div className="m-8">
                    <ButtonBigDown onClick={() => handleCommand('down')} />
                </div>

                <div className="flex">
                    <ButtonLabel
                        label="All"
                        onClick={() => handleAllOrNone(true)}
                    />
                    <ButtonLabel
                        label="None"
                        onClick={() => handleAllOrNone(false)}
                    />
                </div>

                <div className="flex mt-5 text-4xl">
                    {devicesById.map((device) => (
                        <DeviceById
                            key={device.name}
                            name={device.name}
                            selected={device.selected}
                            onClick={() => changeSelected(device.name)}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
