import styles from './device-by-id.module.css';
import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronUp, faChevronDown } from '@fortawesome/free-solid-svg-icons';

type Props = { netId: string; selected?: boolean; onClick?: () => void };

export function DeviceById(props: Props) {
    const dummyCallback = () => true;
    const { netId, selected = true, onClick = dummyCallback } = props;
    const [isSelected, setIsSelected] = useState(false);
    const [classSelected, setClassSelected] = useState('');

    useEffect(() => {
        setIsSelected(selected);
    }, [selected]);

    useEffect(() => {
        if (isSelected) {
            setClassSelected('bg-blue-700');
        } else {
            setClassSelected('border-blue-700');
        }
    }, [isSelected]);

    return (
        <div className={`${styles.component} flex flex-col items-center`}>
            <div className="flex flex-col items-center">
                <button
                    key={netId}
                    className={`${classSelected} rounded-lg m-3 px-4 py-2 border border-transparent focus:outline-none h-20 w-20`}
                    onClick={onClick}
                >
                    {netId}
                </button>
            </div>
        </div>
    );
}
