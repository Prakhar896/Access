import React from 'react'
import withAuth from '../../components/hoc/withAuth'
import { Text } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import withNavbar from '../../components/hoc/withNavbar';

function Directory() {
    const { username } = useSelector(state => state.auth);

    return (
        <Text>Welcome {username}!</Text>
    )
}

export default withAuth(withNavbar(Directory));