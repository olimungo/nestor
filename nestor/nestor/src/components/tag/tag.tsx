import styles from './tag.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { useEffect, useState } from 'react';

type Props = {
    label: string;
    displayClose?: boolean;
    active?: boolean;
    onRemove?: (value: string) => void;
    onClick?: (value: string) => void;
};

const ACTIVE_STYLE = 'bg-red-600';
const INACTIVE_STYLE = 'bg-red-400';

export function Tag(props: Props) {
    const dummyCallback = () => true;
    const {
        label,
        displayClose = false,
        active = false,
        onRemove = dummyCallback,
        onClick = dummyCallback,
    } = props;

    const [activeStyle, setActiveStyle] = useState('');

    useEffect(() => {
        if (active) {
            setActiveStyle(ACTIVE_STYLE);
        } else {
            setActiveStyle(INACTIVE_STYLE);
        }
    }, [active]);

    const handleClick = () => {
        setActiveStyle(
            activeStyle === ACTIVE_STYLE ? INACTIVE_STYLE : ACTIVE_STYLE
        );
        onClick(label);
    };

    return (
        <div
            className={`${styles.component} flex rounded-lg m-2 px-2 cursor-pointer ${activeStyle}`}
            onClick={handleClick}
        >
            <div>{label}</div>
            {displayClose ? (
                <div className="pl-3" onClick={() => onRemove(label)}>
                    <FontAwesomeIcon
                        className="self-center"
                        icon={faTimes}
                        size="1x"
                    />
                </div>
            ) : (
                ''
            )}
        </div>
    );
}
