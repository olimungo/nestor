import styles from './shade.module.css';
import { ButtonBigDown, ButtonBigStop, ButtonBigUp, DeviceById, ButtonLabel } from '@components';
import { IotDevice } from '@models';
import { useEffect, useState } from 'react';

type DeviceByIdType = { id: string; netId: string; selected: boolean };
type Props = {
    devices: IotDevice[];
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
                    id: device.id,
                    netId: device.netId,
                    selected: true,
                }))
                .sort((a, b) => (a.netId > b.netId ? 1 : -1));

            setDevicesById(devicesById);
        }
    }, [devices]);

    const changeSelected = (netId: string) => {
        setDevicesById((previousState) =>
            previousState.map((device) => {
                if (device.netId === netId) {
                    return { id: device.id, netId, selected: !device.selected };
                }

                return device;
            })
        );
    };

    const handleAllOrNone = (selected: boolean) => {
        setDevicesById((previousState) =>
            previousState.map((device) => {
                return { id: device.id, netId: device.netId, selected };
            })
        );
    };

    const handleCommand = (command: string) => {
        devicesById.forEach((device) => {
            if (device.selected) {
                onCommand(device.id, command);
            }
        });
    };

    return (
        <div className={`${styles.component}`}>
            <div className="text-3xl mt-6 ml-6">SHADES</div>

            <div className="flex flex-col items-center w-full">
                <div className="m-5">
                    <ButtonBigUp onClick={() => handleCommand('up')} />
                </div>
                <div className="m-5">
                    <ButtonBigStop onClick={() => handleCommand('stop')} />
                </div>
                <div className="m-5">
                    <ButtonBigDown onClick={() => handleCommand('down')} />
                </div>

                <div className="flex">
                    <ButtonLabel label="All" onClick={() => handleAllOrNone(true)} />
                    <div className="w-4"></div>
                    <ButtonLabel label="None" onClick={() => handleAllOrNone(false)} />
                </div>

                <div className="flex text-4xl">
                    {devicesById.map((device) => (
                        <DeviceById
                            key={device.netId}
                            netId={device.netId}
                            selected={device.selected}
                            onClick={() => changeSelected(device.netId)}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
