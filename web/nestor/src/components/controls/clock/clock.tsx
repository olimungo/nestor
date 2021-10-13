import styles from './clock.module.css';

type Props = {};

export function Clock(props: Props) {
    // const {} = props;

    return (
        <div className={`${styles.component}`}>
            <div className="text-3xl mt-6 ml-6">CLOCK</div>
        </div>
    );
}
