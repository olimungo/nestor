import styles from './devices.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, IotDevice } from '@models';
import { Device } from '@components';
import { useHistory } from 'react-router';

export function Devices() {
    const appContext = useContext(AppContext);
    const history = useHistory();
    const [devices, setDevices] = useState<IotDevice[]>([]);

    useEffect(() => {
        if (appContext.devices) {
            setDevices(appContext.devices.sort((a, b) => (a.id > b.id ? 1 : -1)));
        }
    }, [appContext.devices]);

    const handleEditDevice = (urlId: string) => history.push(`/devices/${urlId}`);

    return (
        <div className={`${styles.component}`}>
            {devices.map((device) => (
                <Device key={device.id} device={device} onEditDevice={handleEditDevice} />
            ))}
        </div>
    );
}
