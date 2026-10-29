export const chatTopics = [
  { id: "ferias", label: "Férias e descanso", prompt: "Quero entender meus direitos sobre férias e descanso. " },
  { id: "jornada", label: "Jornada de trabalho", prompt: "Tenho uma dúvida sobre minha jornada de trabalho. " },
  { id: "decimo-terceiro", label: "13º salário", prompt: "Quero entender como funciona o 13º salário no meu caso. " },
  { id: "horas-extras", label: "Horas extras", prompt: "Tenho uma dúvida sobre horas extras no meu trabalho. " },
  { id: "aviso-previo", label: "Aviso-prévio", prompt: "Quero entender meus direitos sobre aviso-prévio. " },
  { id: "rescisao", label: "FGTS e rescisão", prompt: "Tenho uma dúvida sobre FGTS e rescisão do contrato. " },
] as const;

export function topicChatUrl(topic: (typeof chatTopics)[number]) {
  return `/chat?tema=${topic.id}&q=${encodeURIComponent(topic.prompt)}`;
}
