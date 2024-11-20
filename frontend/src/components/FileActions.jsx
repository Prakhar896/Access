import { Button, FormControl, FormHelperText, FormLabel, HStack, IconButton, Input, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useMediaQuery, VStack } from '@chakra-ui/react'
import { useState } from 'react'
import { BsFillInfoCircleFill, BsInfoCircle, BsPencilFill, BsTrash3Fill } from 'react-icons/bs'
import { FaDownload, FaEllipsisV, FaFileDownload, FaHamburger } from 'react-icons/fa'

function FileActions({ fileData, downloadLinkFor }) {
    const { isOpen: infoModalOpen, onOpen: onInfoModalOpen, onClose: onInfoModalClose } = useDisclosure();
    const { isOpen: renameModalOpen, onOpen: onRenameModalOpen, onClose: onRenameModalClose } = useDisclosure();
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const [newFilename, setNewFilename] = useState('');

    const handleRenameInputEnter = (e) => { if (e.key === 'Enter') renameFile() };
    const handleRenameInputChange = (e) => { setNewFilename(e.target.value) };

    const lastModifiedDate = fileData.originalLastUpdate ? new Date(fileData.originalLastUpdate) : null;
    const uploadedDate = fileData.originalUploadedTimestamp ? new Date(fileData.originalUploadedTimestamp) : null;

    const renameFile = () => {
        console.log("Renaming file to: ", newFilename);
    }

    return (
        <>
            <Menu>
                <MenuButton
                    as={IconButton}
                    aria-label='Options'
                    icon={<FaEllipsisV />}
                    variant='ghost'
                />
                <MenuList>
                    {limitedScreen && (
                        <MenuItem icon={<BsFillInfoCircleFill />} onClick={onInfoModalOpen}>
                            Get Info
                        </MenuItem>
                    )}
                    <MenuItem icon={<FaFileDownload />} onClick={() => location.href = downloadLinkFor(fileData.name)}>
                        Download
                    </MenuItem>
                    <MenuItem icon={<BsPencilFill />} onClick={onRenameModalOpen}>
                        Rename
                    </MenuItem>
                    <MenuDivider />
                    <MenuItem color={'red'} icon={<BsTrash3Fill />}>
                        Delete
                    </MenuItem>
                </MenuList>
            </Menu>

            <Modal onClose={onInfoModalClose} isOpen={infoModalOpen} isCentered size={'sm'}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader fontSize={'md'}>{fileData.name}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <VStack spacing={"10px"} alignItems={"flex-start"}>
                            <Text fontWeight={'bold'}>Name</Text>
                            <Text>{fileData.name}</Text>
                            <Text fontWeight={'bold'}>Last modified</Text>
                            <Text>{lastModifiedDate ? lastModifiedDate.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "medium", hour12: true }) : "Unavailable"}</Text>
                            <Text fontWeight={'bold'}>Uploaded</Text>
                            <Text>{uploadedDate ? uploadedDate.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "medium", hour12: true }) : "Unavailable"}</Text>
                        </VStack>
                    </ModalBody>
                    <ModalFooter>
                        <Button variant={'Default'} onClick={onInfoModalClose}>Got it</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>

            <Modal onClose={onRenameModalClose} isOpen={renameModalOpen} isCentered>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Rename File</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <FormControl>
                            <FormLabel fontFamily={'Ubuntu'}>Enter new filename</FormLabel>
                            <Input type='text' name='newFilename' id='newFilename' placeholder='e.g NewName.pdf' value={newFilename} onChange={handleRenameInputChange} onKeyDown={handleRenameInputEnter} />
                            <FormHelperText fontFamily={'Ubuntu'}>Must be a valid name with file extension and should not already exist.</FormHelperText>
                        </FormControl>
                    </ModalBody>
                    <ModalFooter>
                        <HStack spacing={"10px"}>
                            <Button variant={'ghost'} onClick={onRenameModalClose}>Cancel</Button>
                            <Button variant={'Default'} onClick={renameFile}>Rename</Button>
                        </HStack>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default FileActions