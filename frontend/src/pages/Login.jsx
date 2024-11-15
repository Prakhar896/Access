import { useEffect, useState } from 'react'
import colouredLogo from '/logo/svg/logo-color.svg';
import { AbsoluteCenter, Box, Button, Center, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import configureShowToast from '../components/showToast';
import server from '../networking';
import { fetchSession } from '../slices/AuthState';

function Login() {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const toast = useToast();
    const showToast = configureShowToast(toast);
    const { username, loaded, error } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const [loginLoading, setLoginLoading] = useState(false);
    const [usernameOrEmail, setUsernameOrEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleUsernameOrEmailChange = (e) => { setUsernameOrEmail(e.target.value); }
    const handlePasswordChange = (e) => { setPassword(e.target.value); }
    const handleFieldEnter = (e) => { if (e.key === 'Enter') { login(); } }

    const validateEmail = (text) => {
        return String(text)
            .toLowerCase()
            .match(
                /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            );
    };

    const buttonDisabled = !usernameOrEmail || !password;

    const login = () => {
        if (!usernameOrEmail || !password) {
            showToast('Please fill in all fields', '', 'error');
            return;
        }
        if (usernameOrEmail.indexOf('@') !== -1 && validateEmail(usernameOrEmail) === null) {
            showToast('Invalid email address', '', 'error');
            return;
        }

        const usernameEmailString = usernameOrEmail.trim();
        const passwordText = password.trim();
        setLoginLoading(true);

        server.post('/identity/login', {
            usernameOrEmail: usernameEmailString,
            password: passwordText
        })
            .then(response => {
                if (response.status == 200) {
                    if (response.data && typeof response.data == "string") {
                        if (response.data.startsWith("SUCCESS")) {
                            showToast('Success', 'Logged in successfully!', 'success');
                            dispatch(fetchSession());
                            navigate('/portal/files');
                        } else if (response.data.startsWith("UERROR")) {
                            console.log("User error occurred in login; response:", response.data);
                            showToast("Something went wrong", response.data.substring("UERROR: ".length), 'error');
                        } else {
                            console.log("Unknown response from server in login; response:", response.data);
                            showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                        }
                    } else {
                        console.log("Unexpected response in login; response:", response.data);
                        showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                    }
                } else {
                    console.log("Non-200 status code in login; response:", response.data);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                }

                setLoginLoading(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in login; response:", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), 'error');
                    } else if (err.response.data.startsWith("ERROR")) {
                        console.log("Error occurred in login; response:", err.response.data);
                        showToast("Something went wrong", "Failed to create account. Please try again.", 'error');
                    } else {
                        console.log("Unknown response from server in login; response:", err.response.data);
                        showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                    }
                } else if (err.message) {
                    console.log("Error occurred in login; message:", err.message);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                } else {
                    console.log("Unknown error occurred in login; error:", err);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                }

                setLoginLoading(false);
            })
    }

    useEffect(() => {
        if (username) {
            showToast("You're already signed in", '', 'info');
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
                <Link to={'/'}>
                    <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                </Link>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <ScaleFade in={true} initialScale={0.9}>
                        <Box display={'flex'} flexDir={'column'} alignItems={'center'}>
                            <Heading as={'h1'} size={'xl'}>Jump back in</Heading>
                            <VStack spacing={4} mt={10}>
                                <FormControl id='username' required>
                                    <FormLabel>Username or Email</FormLabel>
                                    <Input onKeyUp={handleFieldEnter} placeholder='e.g johndoe/johndoe@email.com' type='text' w={{ base: 'xs', md: 'md', lg: 'lg' }} value={usernameOrEmail} onChange={handleUsernameOrEmailChange} required />
                                </FormControl>
                                <FormControl id='password' required>
                                    <FormLabel>Password</FormLabel>
                                    <Input onKeyUp={handleFieldEnter} placeholder='Uppercase and numeric letters required' type='password' value={password} onChange={handlePasswordChange} required />
                                </FormControl>
                            </VStack>
                            <VStack mt={'10%'}>
                                <Text>Not a user yet? <Button variant={'link'} color={'black'} onClick={() => navigate('/signup')} >Sign up here.</Button></Text>
                                <Button variant={!buttonDisabled ? 'Default' : 'solid'} w={{ base: 'xs', md: 'md', lg: 'lg' }} onClick={login} isDisabled={buttonDisabled} isLoading={loginLoading}>Sign in</Button>
                            </VStack>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default Login