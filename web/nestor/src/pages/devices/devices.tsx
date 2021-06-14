import styles from './devices.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, DeviceType } from '@declarations';
import { Device } from '@components';

export function Devices() {
    const appContext = useContext(AppContext);
    const [states, setStates] = useState<DeviceType[]>([]);

    useEffect(() => {
        if (appContext.devices) {
            setStates(
                appContext.devices.sort((a, b) => (a.name > b.name ? 1 : -1))
            );
        }
    }, [appContext.devices]);

    return (
        <div className={`${styles.component}`}>
            {states
                ? states.map((device) => (
                      <Device key={device.id} device={device} />
                  ))
                : ''}
        </div>
    );
}
