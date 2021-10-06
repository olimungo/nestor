import styles from './button.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faLongArrowAltLeft,
    faLongArrowAltRight,
    faChevronLeft,
    faChevronRight,
} from '@fortawesome/free-solid-svg-icons';
import { SizeProp } from '@fortawesome/fontawesome-svg-core';

type IconType = 'chevron-left' | 'arrow-left' | 'chevron-right' | 'arrow-right';
type Props = {
    content?: JSX.Element | string;
    icon?: IconType;
    iconSize?: SizeProp;
    colorClassBackground?: string;
    colorClassBackgroundFocus?: string;
    onClick?: () => void;
};

export function Button(props: Props) {
    const {
        content = '',
        icon,
        iconSize = '1x',
        colorClassBackground = '',
        colorClassBackgroundFocus = '',
        onClick,
    } = props;

    return (
        <div className={`${styles.component}`}>
            <button
                onClick={onClick}
                className={`${styles.button} ${colorClassBackground} hover:${colorClassBackgroundFocus}
                    shadow-sm text-gray-100 px-6 py-2 flex items-center rounded-xl
                    focus:outline-none`}
            >
                {icon === 'arrow-left' ? (
                    <FontAwesomeIcon
                        className="mr-3"
                        icon={faLongArrowAltLeft}
                        size={iconSize}
                    />
                ) : (
                    ''
                )}
                {icon === 'chevron-left' ? (
                    <FontAwesomeIcon
                        className="mr-3"
                        icon={faChevronLeft}
                        size={iconSize}
                    />
                ) : (
                    ''
                )}

                <div>{content}</div>

                {icon === 'arrow-right' ? (
                    <FontAwesomeIcon
                        className="ml-3"
                        icon={faLongArrowAltRight}
                        size={iconSize}
                    />
                ) : (
                    ''
                )}
                {icon === 'chevron-right' ? (
                    <FontAwesomeIcon
                        className="ml-3"
                        icon={faChevronRight}
                        size={iconSize}
                    />
                ) : (
                    ''
                )}
            </button>
        </div>
    );
}
