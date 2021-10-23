import styles from './controls.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, IotDevice, IotDeviceType } from '@models';
import { Sign, Shade, Clock, Switch } from '@components';

export function Controls() {
    const appContext = useContext(AppContext);
    const [devices, setDevices] = useState<IotDevice[]>([]);
    const [deviceType, setDeviceType] = useState<IotDeviceType>();

    useEffect(() => {
        if (appContext.store.selectedGroup) {
            setDeviceType(appContext.store.selectedGroup.type);
            setDevices(appContext.store.selectedGroup.devices);
        }
    }, [appContext.store.selectedGroup]);

    const handleCommand = (id: string, command: string) =>
        appContext.socket?.emit('mqtt-command', {
            device: id,
            command,
        });

    return (
        <div className={`${styles.component} text-white`}>
            {deviceType === 'SHADE' ? <Shade devices={devices} onCommand={handleCommand} /> : ''}
            {deviceType === 'SIGN' ? <Sign /> : ''}
            {deviceType === 'CLOCK' ? <Clock devices={devices} onCommand={handleCommand} /> : ''}
            {deviceType === 'SWITCH' ? <Switch devices={devices} onCommand={handleCommand} /> : ''}
        </div>
    );
}
