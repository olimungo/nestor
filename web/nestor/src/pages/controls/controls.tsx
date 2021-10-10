import styles from './controls.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, IotDevice, IotDeviceType } from '@models';
import { Sign, Shade, Clock, Switch } from '@components';

export function Controls() {
    const appContext = useContext(AppContext);
    const [selectedDevices, setSelectedDevices] = useState<IotDevice[]>([]);
    const [id, setId] = useState<IotDeviceType>();

    useEffect(() => {
        if (appContext.selectedGroup) {
            setId(appContext.selectedGroup.type);
            setSelectedDevices(appContext.selectedGroup.devices);
        }
    }, [appContext.selectedGroup]);

    const handleCommand = (id: string, command: string) => {
        appContext.socket?.emit('mqtt-command', {
            device: id,
            command,
        });
    };

    return (
        <div className={`${styles.component} text-white`}>
            {id === 'SHADE' ? <Shade devices={selectedDevices} onCommand={handleCommand} /> : ''}
            {id === 'SIGN' ? <Sign /> : ''}
            {id === 'CLOCK' ? <Clock /> : ''}
            {id === 'SWITCH' ? <Switch /> : ''}
        </div>
    );
}
