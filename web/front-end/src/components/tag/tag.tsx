import styles from './tag.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { MouseEvent, useEffect, useState } from 'react';

type Props = {
    label: string;
    displayClose?: boolean;
    enableClick?: boolean;
    active?: boolean;
    onRemove?: (value: string) => void;
    onClick?: (value: string) => void;
};

const ACTIVE_STYLE = 'bg-green-600';
const INACTIVE_STYLE = 'bg-yellow-500';

export function Tag(props: Props) {
    const dummyCallback = () => true;
    const {
        label,
        displayClose = false,
        enableClick = false,
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
        if (enableClick) {
            setActiveStyle(activeStyle === ACTIVE_STYLE ? INACTIVE_STYLE : ACTIVE_STYLE);
            onClick(label);
        }
    };

    const handleRemove = (event: MouseEvent<HTMLDivElement>) => {
        event.stopPropagation();
        onRemove(label);
    };

    return (
        <div
            className={`${styles.component} flex rounded-lg mr-3 mt-3 py-2 px-4 cursor-pointer text-xl ${activeStyle}`}
            onClick={handleClick}
        >
            <div className="text-white">{label}</div>
            {displayClose ? (
                <div className="pl-3" onClick={handleRemove}>
                    <FontAwesomeIcon className="self-center" icon={faTimes} size="1x" />
                </div>
            ) : (
                ''
            )}
        </div>
    );
}
