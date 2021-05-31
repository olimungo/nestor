import styles from './pure-input.module.css';
import { ChangeEvent, useEffect, useState } from 'react';

const LABEL_UP_STYLE = { top: '-1em', fontSize: '.5em' };
const LABEL_TRANSITION_STYLE = { transition: '0.2s ease-out' };

type InputSize = 'tiny' | 'small' | 'medium' | 'regular' | 'large' | 'full';
type InputType = 'text' | 'number' | 'email' | 'password' | 'date';
type ThemeType = 'light' | 'dark';

type Props = {
    value?: string;
    size?: InputSize;
    type?: InputType;
    placeholder?: string;
    minLength?: number;
    maxLength?: number;
    onChange?: (value: string) => void;
    theme?: ThemeType;
};

export function PureInput(props: Props) {
    const dummyCallback = () => true;
    const {
        value = '',
        size = 'regular',
        type = 'text',
        placeholder = '',
        minLength = -1,
        maxLength = -1,
        onChange = dummyCallback,
        theme = 'light',
    } = props;
    const [width, setWidth] = useState({});
    const [labelUpStyle, setLabelUpStyle] = useState({});
    const [labelTransitionStyle, setLabelTransitionStyle] = useState({});
    const [inputValue, setInputValue] = useState('');
    const [borderColor, setBorderColor] = useState('');
    const [labelColor, setLabelColor] = useState('');
    const [inputColor, setInputColor] = useState('');

    useEffect(() => {
        setInputValue(value);

        if (value) {
            setLabelUpStyle(LABEL_UP_STYLE);
        } else {
            setLabelUpStyle({});
        }

        // Let the component refresh once before applying the effect on the label,
        // so it doesn't happen at the initialisation of the element if it gets an
        // initial value
        setTimeout(() => {
            setLabelTransitionStyle(LABEL_TRANSITION_STYLE);
        }, 0);
    }, [value]);

    useEffect(() => {
        switch (size) {
            case 'tiny':
                setWidth({ width: '3rem' });
                break;
            case 'small':
                setWidth({ width: '5rem' });
                break;
            case 'medium':
                setWidth({ width: '9rem' });
                break;
            case 'regular':
                setWidth({ width: '17rem' });
                break;
            case 'large':
                setWidth({ width: '33rem' });
                break;
            case 'full':
                setWidth({ width: '100%' });
                break;
        }
    }, [size]);

    useEffect(() => {
        if (theme === 'dark') {
            setBorderColor('border-black');
            setLabelColor('text-gray-400');
            setInputColor('text-gray-600');
        } else {
            setBorderColor('border-white');
            setLabelColor('text-yellow-100');
            setInputColor('text-yellow-50');
        }
    }, [theme]);

    const id =
        'input' +
        new Date().getTime().toString() +
        Math.floor(Math.random() * 100).toString();

    const handleBlur = () => {
        if (!inputValue) {
            setLabelUpStyle({});
        }
    };

    const handleFocus = () => setLabelUpStyle(LABEL_UP_STYLE);

    const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
        onChange(event.currentTarget.value);
        setInputValue(event.currentTarget.value);
    };

    return (
        <div className={`${styles.component} text-left p-5`}>
            <div className="relative">
                <label
                    htmlFor={id}
                    className={`${labelColor} absolute box-border top-0`}
                    style={{ ...labelUpStyle, ...labelTransitionStyle }}
                >
                    {placeholder}
                </label>

                <input
                    id={id}
                    type={type}
                    minLength={minLength}
                    maxLength={maxLength}
                    value={inputValue}
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                    onChange={handleChange}
                    className={`${borderColor} ${inputColor} bg-transparent border-b box-border outline-none border-opacity-20`}
                    style={width}
                />
            </div>
        </div>
    );
}
