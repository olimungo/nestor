import styles from './controls.module.css';
import { useContext, useEffect, useState } from 'react';
import { AppContext, DeviceType, DeviceTypes } from '@declarations';
import {
    MotorV,
    MotorH,
    DoubleSwitch,
    Slider,
    StepperH,
    StepperV,
    Switch,
} from '@components';

type Props = { onCommand?: (name: string, command: string) => void };

export function Controls(props: Props) {
    const dummyCallback = () => true;
    const { onCommand = dummyCallback } = props;
    const appContext = useContext(AppContext);
    const [selectedDevices, setSelectedDevices] = useState<DeviceType[]>([]);
    const [id, setId] = useState<Number>(-1);

    useEffect(() => {
        if (appContext.selectedDevices) {
            setId(appContext.selectedDevices.id);
            setSelectedDevices(appContext.selectedDevices.devices);
        }
    }, [appContext.selectedDevices]);

    return (
        <div className={`${styles.component} text-white`}>
            {id === DeviceTypes.DOUBLE_SWITCH ? <DoubleSwitch /> : ''}
            {id === DeviceTypes.MOTOR_V ? (
                <MotorV devices={selectedDevices} onCommand={onCommand} />
            ) : (
                ''
            )}
            {id === DeviceTypes.MOTOR_H ? <MotorH /> : ''}
            {id === DeviceTypes.SLIDER ? <Slider /> : ''}
            {id === DeviceTypes.STEPPER_H ? <StepperH /> : ''}
            {id === DeviceTypes.STEPPER_V ? <StepperV /> : ''}
            {id === DeviceTypes.SWITCH ? <Switch /> : ''}
        </div>
    );
}
