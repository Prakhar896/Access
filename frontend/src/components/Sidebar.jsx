import { Button, Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay, Flex, Image, Text, Icon, Box, useDisclosure, useToast, DrawerFooter, HStack } from '@chakra-ui/react'
import { BsQuestionCircle } from 'react-icons/bs';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import colouredLogo from '/logo/svg/logo-color.svg';
import configureShowToast from "../components/showToast"
import { FaFile, FaRegClipboard, FaUser } from 'react-icons/fa';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUpFromBracket, faFile } from '@fortawesome/free-solid-svg-icons';
import UploadFilesModal from './UploadFilesModal';

function Sidebar({ isOpen, onClose }) {
    const navigate = useNavigate();

    const toast = useToast();
    const showToast = configureShowToast(toast)
    const { isOpen: isUploadFilesModalOpen, onOpen: onUploadFilesModalOpen, onClose: onUploadFilesModalClose } = useDisclosure();

    const DrawerHover = {
        _hover: {
            bg: "#E4EBF8"
        },
        borderRadius: "20px",
    };

    const handleModalOpen = () => {
        onClose();
        onUploadFilesModalOpen();
    }

    return (
        <>
            <Drawer
                isOpen={isOpen}
                placement='left'
                onClose={onClose}
            >
                <DrawerOverlay />
                <DrawerContent>
                    <DrawerCloseButton />
                    <DrawerHeader>
                        <Flex justifyContent="center" alignItems="center" height="100px">
                            <Image src={colouredLogo} height="70px" maxWidth="70px" rounded={'xl'} />
                        </Flex>
                    </DrawerHeader>

                    <DrawerBody display={"flex"} flexDirection={"column"}>
                        <Button color={"#515F7C"} mb={2} justifyContent={"left"} colorScheme='white' sx={DrawerHover}>
                            <HStack>
                                <Box ml={'5px'}>
                                    <FaFile />
                                </Box>
                                <Text ml={2}>My Files</Text>
                            </HStack>
                        </Button>

                        <Button color="#515F7C" mb={2} justifyContent={"left"} colorScheme='white' sx={DrawerHover}>
                            <HStack>
                                <Box ml={'5px'}>
                                    <FaUser />
                                </Box>
                                <Text ml={2}>My Account</Text>
                            </HStack>
                        </Button>

                        <Box position="absolute" bottom="0" textAlign="center" ml={14} mb={2}>
                            <Text color={"#515F7C"}>© 2024 Prakhar Trivedi</Text>
                        </Box>
                    </DrawerBody>
                    <DrawerFooter display="flex" justifyContent="center">
                        <Box mb={4}>
                            <Button variant="Default" mb={4} onClick={handleModalOpen}>
                                <HStack spacing={'10px'}>
                                    <FontAwesomeIcon icon={faArrowUpFromBracket} />
                                    <Text>Upload Files</Text>
                                </HStack>
                            </Button>
                        </Box>
                    </DrawerFooter>
                </DrawerContent>
            </Drawer>
            <UploadFilesModal isOpen={isUploadFilesModalOpen} onOpen={onUploadFilesModalOpen} onClose={onUploadFilesModalClose} />
        </>
    )
}

export default Sidebar;