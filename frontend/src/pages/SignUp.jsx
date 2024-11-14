import { useEffect, useState } from 'react'
import colouredLogo from '/logo/svg/logo-color.svg';
import { AbsoluteCenter, Box, Button, Center, FormControl, FormLabel, Heading, Image, Input, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import configureShowToast from '../components/showToast';

function SignUp() {
    const navigate = useNavigate();
    const toast = useToast();
    const showToast = configureShowToast(toast);
    const { username, loaded, error } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    useEffect(() => {
        if (username) {
            navigate('/');
        }
    }, [username, loaded])

    if (!loaded) {
        return <Center h={'100vh'}><Spinner /></Center>
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <Box display={'flex'} flexDirection={'column'} justifyContent={'space-between'} alignItems={'center'} mt={!limitedScreen ? '10%' : '20%'}>
                <Spacer />
                <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <Heading as={'h1'} size={'xl'}>Create an account</Heading>
                    <VStack spacing={4} mt={10}>
                        <FormControl id='email' required>
                            <FormLabel>Email</FormLabel>
                            <Input placeholder='e.g john@example.com' type='email' w={{ base: 'xs', md: 'md', lg: 'lg'}} required />
                        </FormControl>
                        <FormControl id='password' required>
                            <FormLabel>Password</FormLabel>
                            <Input placeholder='Uppercase and numeric letters required' type='password' required />
                        </FormControl>
                        <FormControl id='confirmPassword' required>
                            <FormLabel>Confirm Password</FormLabel>
                            <Input placeholder='Re-enter your password' type='confirmPassword' required />
                        </FormControl>
                    </VStack>
                    <Button variant={'Default'} w={{ base: 'xs', md: 'md', lg: 'lg'}} mt={'10%'}>Get Started</Button>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default SignUp