import styles from './device-by-id.module.css';
import { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronUp, faChevronDown } from '@fortawesome/free-solid-svg-icons';

type Props = { name: string; selected?: boolean; onClick?: () => void };

export function DeviceById(props: Props) {
    const dummyCallback = () => true;
    const { name, selected = true, onClick = dummyCallback } = props;
    const [id, setId] = useState<number | undefined>();
    const [isSelected, setIsSelected] = useState(false);
    const [classSelected, setClassSelected] = useState('');
    const [isChevronUpVisible, setIsChevronUpVisible] = useState(false);
    const [isChevronDownVisible, setIsChevronDownVisible] = useState(false);

    useEffect(() => {
        if (name) {
            setId(parseInt(name.split('/')[1]));
        }
    }, [name]);

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
                <FontAwesomeIcon
                    className={isChevronUpVisible ? 'visible' : 'invisible'}
                    icon={faChevronUp}
                />

                <button
                    key={id}
                    className={`${classSelected} rounded m-3 px-4 py-2 border border-transparent focus:outline-none h-20 w-20`}
                    onClick={onClick}
                >
                    {id}
                </button>

                <FontAwesomeIcon
                    className={isChevronDownVisible ? 'visible' : 'invisible'}
                    icon={faChevronDown}
                />
            </div>
        </div>
    );
}
