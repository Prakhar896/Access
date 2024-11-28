import { Button, Text } from '@chakra-ui/react'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { changeSystemVersion } from '../slices/UniversalState';
import server from '../networking';

function Version() {
    const dispatch = useDispatch();
    const Universal = useSelector(state => state.universal)

    const changeVersion = () => {
        dispatch(changeSystemVersion(prompt("Enter version:")))
    }

    useEffect(() => {
        server.get('/version').then(response => {
            dispatch(changeSystemVersion(response.data))
        }).catch(e => console.error(e));
    }, [])

    return <>
        <Text>{Universal.systemVersion}</Text>
        <Button onClick={changeVersion}>Change</Button>
    </>
}

export default Version