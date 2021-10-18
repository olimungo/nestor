import styles from './device-selector.module.css';
import { IotDeviceById } from '@models';
import { ButtonLabel, DeviceById } from '@components';
import { useEffect, useState } from 'react';

type Props = {
    devices: IotDeviceById[];
    onChange: (devicesById: IotDeviceById[]) => void;
};

export function DeviceSelector(props: Props) {
    const dummyCallback = () => true;
    const { devices, onChange = dummyCallback } = props;

    const [devicesById, setDevicesById] = useState<IotDeviceById[]>([]);

    useEffect(() => {
        if (devices) {
            setDevicesById(devices);
        }
    }, [devices]);

    const changeSelected = (netId: string) => {
        setDevicesById((previousState) => {
            const state = previousState.map((device) => {
                if (device.netId === netId) {
                    return { id: device.id, netId, selected: !device.selected };
                }

                return device;
            });

            onChange(state);

            return state;
        });
    };

    const handleAllOrNone = (selected: boolean) => {
        setDevicesById((previousState) => {
            const state = previousState.map((device) => ({
                id: device.id,
                netId: device.netId,
                selected,
            }));

            onChange(state);

            return state;
        });
    };

    return (
        <div className={`${styles.component} text-white m-5`}>
            <div className="flex justify-center mt-10">
                <ButtonLabel label="All" onClick={() => handleAllOrNone(true)} />
                <div className="w-4"></div>
                <ButtonLabel label="None" onClick={() => handleAllOrNone(false)} />
            </div>

            <div className="flex justify-center text-4xl">
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
    );
}
