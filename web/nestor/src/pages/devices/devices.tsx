import styles from './devices.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, IotDevice } from '@models';
import { Device } from '@components';

export function Devices() {
    const appContext = useContext(AppContext);
    const [devices, setDevices] = useState<IotDevice[]>([]);

    useEffect(() => {
        if (appContext.devices) {
            setDevices(
                appContext.devices.sort((a, b) => (a.id > b.id ? 1 : -1))
            );
        }
    }, [appContext.devices]);

    return (
        <div className={`${styles.component}`}>
            {devices.map((device) => (<Device key={device.id} device={device} />))}
        </div>
    );
}
