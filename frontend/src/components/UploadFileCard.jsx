import { Box, Button, Card, Spacer, Spinner, Text, VStack } from '@chakra-ui/react'
import { BsFillCheckCircleFill } from 'react-icons/bs';
import { FaTrash } from 'react-icons/fa';

function UploadFileCard({ index, fileName, uploading, uploadResults, handleRemoveFile }) {
    const uploadMessage = typeof uploadResults == "object" && uploadResults[fileName] !== undefined ? uploadResults[fileName] : null;
    const success = uploadMessage && uploadMessage.startsWith("SUCCESS");
    const successUpdate = uploadMessage && uploadMessage.startsWith("SUCCESS: File updated") ? uploadMessage.substring("SUCCESS: ".length) : null;
    const uerrorMessage = uploadMessage && uploadMessage.startsWith("UERROR") ? uploadMessage.substring("UERROR: ".length) : null;

    return (
        <Card key={index} mb={2} padding={"13px"} display="flex" flexDirection={"row"} alignItems={'center'} justifyContent={"space-between"}>
                {uploading && <Spinner />}
                {success && (
                    <BsFillCheckCircleFill color={'lime'} size={'20px'} />
                )}
                <VStack justifyContent={'left'} alignItems={'center'} textAlign={'left'} h={'100%'} ml={"20px"}>
                    <Text fontSize={"15px"} textOverflow={"ellipsis"} w={'100%'}>
                        {fileName}
                    </Text>
                    {(uerrorMessage || successUpdate) && (
                        <Text fontSize={"15px"} color={successUpdate ? 'green': 'red'} textAlign={'left'} w={'100%'}>
                            {uerrorMessage || successUpdate || "Unknown error occurred."}
                        </Text>
                    )}
                </VStack>
                <Spacer />
                {!uploading ? (
                    <Button onClick={() => handleRemoveFile(index)} color={'red'}>
                        <FaTrash />
                    </Button>
                ) : (
                    <Spacer />
                )}
        </Card>
    )
}

export default UploadFileCard